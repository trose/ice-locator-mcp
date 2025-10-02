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
  UpdateDistributionRequest,
  UpdateDistributionResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface UpdateDistributionCommandInput
  extends UpdateDistributionRequest {}
export interface UpdateDistributionCommandOutput
  extends UpdateDistributionResult,
    __MetadataBearer {}
export declare class UpdateDistributionCommand extends $Command<
  UpdateDistributionCommandInput,
  UpdateDistributionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: UpdateDistributionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: UpdateDistributionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<UpdateDistributionCommandInput, UpdateDistributionCommandOutput>;
  private serialize;
  private deserialize;
}
