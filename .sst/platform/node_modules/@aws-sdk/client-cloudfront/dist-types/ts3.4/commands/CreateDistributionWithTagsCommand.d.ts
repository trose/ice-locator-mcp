import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  CreateDistributionWithTagsRequest,
  CreateDistributionWithTagsResult,
} from "../models/models_0";
export { __MetadataBearer, $Command };
export interface CreateDistributionWithTagsCommandInput
  extends CreateDistributionWithTagsRequest {}
export interface CreateDistributionWithTagsCommandOutput
  extends CreateDistributionWithTagsResult,
    __MetadataBearer {}
export declare class CreateDistributionWithTagsCommand extends $Command<
  CreateDistributionWithTagsCommandInput,
  CreateDistributionWithTagsCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: CreateDistributionWithTagsCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: CreateDistributionWithTagsCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    CreateDistributionWithTagsCommandInput,
    CreateDistributionWithTagsCommandOutput
  >;
  private serialize;
  private deserialize;
}
