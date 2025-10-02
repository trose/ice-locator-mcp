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
  CreateDistributionRequest,
  CreateDistributionResult,
} from "../models/models_0";
export { __MetadataBearer, $Command };
export interface CreateDistributionCommandInput
  extends CreateDistributionRequest {}
export interface CreateDistributionCommandOutput
  extends CreateDistributionResult,
    __MetadataBearer {}
export declare class CreateDistributionCommand extends $Command<
  CreateDistributionCommandInput,
  CreateDistributionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: CreateDistributionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: CreateDistributionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<CreateDistributionCommandInput, CreateDistributionCommandOutput>;
  private serialize;
  private deserialize;
}
