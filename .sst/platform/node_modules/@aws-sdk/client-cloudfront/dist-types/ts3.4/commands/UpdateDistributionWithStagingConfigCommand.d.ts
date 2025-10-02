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
  UpdateDistributionWithStagingConfigRequest,
  UpdateDistributionWithStagingConfigResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface UpdateDistributionWithStagingConfigCommandInput
  extends UpdateDistributionWithStagingConfigRequest {}
export interface UpdateDistributionWithStagingConfigCommandOutput
  extends UpdateDistributionWithStagingConfigResult,
    __MetadataBearer {}
export declare class UpdateDistributionWithStagingConfigCommand extends $Command<
  UpdateDistributionWithStagingConfigCommandInput,
  UpdateDistributionWithStagingConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: UpdateDistributionWithStagingConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: UpdateDistributionWithStagingConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    UpdateDistributionWithStagingConfigCommandInput,
    UpdateDistributionWithStagingConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
